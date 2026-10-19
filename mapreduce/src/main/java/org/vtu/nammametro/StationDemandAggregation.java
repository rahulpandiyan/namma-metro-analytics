package org.vtu.nammametro;

import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * VTU 7th Semester Big Data Analytics (BCS714D) - Project MapReduce Job 1
 * 
 * Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
 * Job 1: Station-wise Passenger Demand Aggregation
 * 
 * Aggregates total passenger boardings (entries) and alightings (exits) 
 * across all Bengaluru metro stations.
 * 
 * Input format (CSV, ';' delimited):
 *   Date;Hour;Station;Ridership
 * 
 * Output format:
 *   StationName \t TotalPassengerDemand
 */
public class StationDemandAggregation {

    public static class DemandMapper extends Mapper<LongWritable, Text, Text, LongWritable> {
        private final Text stationKey = new Text();
        private final LongWritable ridershipVal = new LongWritable();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty() || line.startsWith("Date;") || line.startsWith("Date,")) {
                return; // Skip empty lines and CSV header
            }

            // Split by ';' (standard for BMRCL dataset) or fallback to ','
            String[] tokens = line.contains(";") ? line.split(";") : line.split(",");
            if (tokens.length >= 4) {
                try {
                    String station = tokens[2].trim();
                    long ridership = Long.parseLong(tokens[3].trim());
                    if (!station.isEmpty() && ridership > 0) {
                        stationKey.set(station);
                        ridershipVal.set(ridership);
                        context.write(stationKey, ridershipVal);
                    }
                } catch (NumberFormatException ignored) {
                    // Skip malformed records
                }
            }
        }
    }

    public static class DemandReducer extends Reducer<Text, LongWritable, Text, LongWritable> {
        private final LongWritable totalDemand = new LongWritable();

        @Override
        protected void reduce(Text key, Iterable<LongWritable> values, Context context)
                throws IOException, InterruptedException {
            long sum = 0;
            for (LongWritable val : values) {
                sum += val.get();
            }
            totalDemand.set(sum);
            context.write(key, totalDemand);
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: StationDemandAggregation <input_path> <output_path>");
            System.exit(1);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Namma Metro - Station Demand Aggregation");
        job.setJarByClass(StationDemandAggregation.class);

        job.setMapperClass(DemandMapper.class);
        job.setCombinerClass(DemandReducer.class);
        job.setReducerClass(DemandReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(LongWritable.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        boolean success = job.waitForCompletion(true);
        System.exit(success ? 0 : 1);
    }
}
