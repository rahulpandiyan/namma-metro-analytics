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
 * VTU 7th Semester Big Data Analytics (BCS714D) - Project MapReduce Job 3
 * 
 * Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
 * Job 3: Origin-Destination Station-Pair Ranking
 * 
 * Aggregates passenger volumes and estimated fare revenues for every 
 * origin-to-destination corridor across the Bengaluru metro network.
 * 
 * Input format (CSV, ';' delimited):
 *   Date;Hour;Origin Station;Destination Station;Ridership;Travelled Stations;Fare Slab;Fare;Revenue
 * 
 * Output format:
 *   Origin -> Destination \t TotalRidership \t TotalRevenue
 */
public class StationPairRanking {

    public static class PairMapper extends Mapper<LongWritable, Text, Text, Text> {
        private final Text pairKey = new Text();
        private final Text metricVal = new Text();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty() || line.startsWith("Date;") || line.startsWith("Date,")) {
                return;
            }

            String[] tokens = line.contains(";") ? line.split(";") : line.split(",");
            if (tokens.length >= 9) {
                try {
                    String origin = tokens[2].trim();
                    String destination = tokens[3].trim();
                    long ridership = Long.parseLong(tokens[4].trim());
                    long revenue = Long.parseLong(tokens[8].trim());

                    if (!origin.isEmpty() && !destination.isEmpty() && ridership > 0) {
                        pairKey.set(origin + " -> " + destination);
                        metricVal.set(ridership + "," + revenue);
                        context.write(pairKey, metricVal);
                    }
                } catch (NumberFormatException ignored) {
                }
            }
        }
    }

    public static class PairReducer extends Reducer<Text, Text, Text, Text> {
        private final Text resultText = new Text();

        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            long totalRidership = 0;
            long totalRevenue = 0;

            for (Text val : values) {
                String[] parts = val.toString().split(",");
                if (parts.length >= 2) {
                    try {
                        totalRidership += Long.parseLong(parts[0].trim());
                        totalRevenue += Long.parseLong(parts[1].trim());
                    } catch (NumberFormatException ignored) {
                    }
                }
            }

            resultText.set(totalRidership + "\tINR " + totalRevenue);
            context.write(key, resultText);
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: StationPairRanking <input_path> <output_path>");
            System.exit(1);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Namma Metro - Station Pair Journey Ranking");
        job.setJarByClass(StationPairRanking.class);

        job.setMapperClass(PairMapper.class);
        job.setReducerClass(PairReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        boolean success = job.waitForCompletion(true);
        System.exit(success ? 0 : 1);
    }
}
